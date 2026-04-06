package com.autograder.backend.controller;

import com.autograder.backend.service.MLServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.*;

/**
 * GradingOrchestrationController
 *
 * Single endpoint that runs the full Vision-First pipeline:
 * 1. Crop instructor zones (visual ground truth)
 * 2. Crop student zones (with alignment confidence)
 * 3. Serial-with-Delay grade each zone (Demo Resilience)
 * 4. Generate class analytics summary
 */
@RestController
@RequestMapping("/api/grading")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
@Slf4j
public class GradingOrchestrationController {

    private final MLServiceClient mlServiceClient;

    @PostMapping("/run")
    public ResponseEntity<?> runGrading(
            @RequestParam("template") MultipartFile templateFile,
            @RequestParam("instructor") MultipartFile instructorFile,
            @RequestParam("student") MultipartFile studentFile,
            @RequestParam(value = "rubric", required = false) String formRubric) {

        try {
            log.info("=== Grading pipeline started ===");

            // ── Step 1: Crop instructor zones ───────────────────────────────
            log.info("Step 1: Cropping instructor zones...");
            Map<String, Object> instructorResponse = mlServiceClient.cropZones(templateFile, instructorFile);
            @SuppressWarnings("unchecked")
            Map<String, String> instructorCrops = (Map<String, String>) instructorResponse.get("crops");
            if (instructorCrops == null || instructorCrops.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "No answer zones found in instructor key."));
            }

            // ── Step 2: Crop student zones ──────────────────────────────────
            log.info("Step 2: Cropping student zones...");
            Map<String, Object> studentResponse = mlServiceClient.cropZones(templateFile, studentFile);
            @SuppressWarnings("unchecked")
            Map<String, String> studentCrops = (Map<String, String>) studentResponse.get("crops");
            double alignmentConfidence = studentResponse.containsKey("alignment_confidence")
                    ? ((Number) studentResponse.get("alignment_confidence")).doubleValue()
                    : 0.0;
            if (studentCrops == null || studentCrops.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "Could not align student paper to template."));
            }
            log.info("Zones found: {} | Alignment: {}", studentCrops.keySet(), alignmentConfidence);

            // ── Step 3: Resilient Serial Grading (15s cool-down) ──────────
            log.info("Step 3: Running serial grading ({} zones) with cool-downs...", studentCrops.size());
            String rubric = (formRubric != null && !formRubric.trim().isEmpty()) ? formRubric : "Grade the student answer mathematically by comparing it VISUALLY to the instructor's key. Be objective.";
            List<Map<String, Object>> gradingResults = new ArrayList<>();

            for (Map.Entry<String, String> entry : studentCrops.entrySet()) {
                String zoneId = entry.getKey();
                log.info("Grading Zone {}...", zoneId);
                
                try {
                    Map<String, Object> result = mlServiceClient.gradeSingleZone(
                        "STUDENT_001", zoneId, entry.getValue(), instructorCrops.get(zoneId), rubric
                    );
                    
                    if (result != null) {
                        Map<String, Object> normalized = new HashMap<>();
                        normalized.put("student_id", "STUDENT_001");
                        normalized.put("zone_id", zoneId);
                        normalized.put("score", result.get("total_score"));
                        normalized.put("max_score", result.get("max_score"));
                        normalized.put("confidence", result.get("overall_confidence"));
                        normalized.put("reasoning", result.get("reasoning")); // ⚡ FIXED: Mapping actual AI reasoning
                        normalized.put("concept", result.get("discovered_concept"));
                        gradingResults.add(normalized);
                    }
                    
                    if (gradingResults.size() < studentCrops.size()) {
                        log.info("Cooling down for 15s to preserve API quota...");
                        Thread.sleep(15000);
                    }
                } catch (Exception e) {
                    log.error("Failed to grade zone {}: {}", zoneId, e.getMessage());
                }
            }

            if (gradingResults.isEmpty()) {
                return ResponseEntity.internalServerError().body(Map.of("error", "Grading engine failed to return results."));
            }

            // ── Step 4: Analytics and Final Response ────────────────────────
            log.info("Step 4: Generating analytics...");
            Map<String, Object> analytics = mlServiceClient.getAnalytics(gradingResults);

            Map<String, Object> response = new LinkedHashMap<>();
            response.put("alignment_confidence", alignmentConfidence);
            response.put("zones_graded", gradingResults.size());
            response.put("per_zone_scores", gradingResults);
            response.put("analytics", analytics);

            log.info("=== Grading pipeline complete ===");
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("Pipeline failed", e);
            return ResponseEntity.internalServerError().body(Map.of("error", "Pipeline error: " + e.getMessage()));
        }
    }
}
