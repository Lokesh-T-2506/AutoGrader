package com.autograder.backend.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

import java.io.IOException;
import java.util.List;
import java.util.Map;

/**
 * MLServiceClient v2 — Vision-First Pipeline
 * Matches the actual endpoints used by demo_harness.py.
 */
@Service
public class MLServiceClient {

    private final WebClient webClient;

    @Value("${ml-service.ocr.url}")
    private String ocrUrl;

    @Value("${ml-service.grading.url}")
    private String gradingUrl;

    @Value("${ml-service.analytics.url}")
    private String analyticsUrl;

    public MLServiceClient(WebClient.Builder builder) {
        this.webClient = builder
                .codecs(c -> c.defaultCodecs().maxInMemorySize(50 * 1024 * 1024))
                .build();
    }

    /**
     * Step 1: Send two images to the OCR service (Template + Target).
     * Returns a map of zone_id → base64 JPEG crop string + alignment metadata.
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> cropZones(MultipartFile templateFile, MultipartFile targetFile) throws IOException {
        MultipartBodyBuilder body = new MultipartBodyBuilder();

        body.part("template_file", new ByteArrayResource(templateFile.getBytes()) {
            @Override public String getFilename() { return templateFile.getOriginalFilename(); }
        }).contentType(MediaType.IMAGE_PNG);

        body.part("target_file", new ByteArrayResource(targetFile.getBytes()) {
            @Override public String getFilename() { return targetFile.getOriginalFilename(); }
        }).contentType(MediaType.IMAGE_PNG);

        return webClient.post()
                .uri(ocrUrl + "/api/ocr/crop-zones")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(body.build()))
                .retrieve()
                .bodyToMono(Map.class)
                .block(java.time.Duration.ofSeconds(300));
    }

    /**
     * Step 2 (Option A): Single-zone grading (Resilient Demo Mode).
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> gradeSingleZone(String studentId,
                                                String zoneId,
                                                String imageB64,
                                                String referenceImageB64,
                                                String rubric) {
        Map<String, Object> payload = Map.of(
                "student_image_b64", imageB64,
                "reference_image_b64", referenceImageB64 != null ? referenceImageB64 : "",
                "reference_solution", "Instructor solution provided in image.",
                "rubric_text", rubric,
                "question_text", "Zone " + zoneId
        );

        return webClient.post()
                .uri(gradingUrl + "/api/grade/vision")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(payload)
                .retrieve()
                .bodyToMono(Map.class)
                .block(java.time.Duration.ofSeconds(300));
    }

    /**
     * Step 2 (Option B): Batch vision grading.
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> batchGrade(String studentId, Map<String, Object> zones, String rubric) {
        Map<String, Object> payload = Map.of(
                "student_id", studentId,
                "zones", zones,
                "rubric", rubric
        );

        return (List<Map<String, Object>>) (List<?>) webClient.post()
                .uri(gradingUrl + "/api/grade/batch-vision")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(payload)
                .retrieve()
                .bodyToMono(List.class)
                .block(java.time.Duration.ofSeconds(300));
    }

    /**
     * Step 3: Class analytics aggregation.
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getAnalytics(List<Map<String, Object>> results) {
        Map<String, Object> payload = Map.of("results", results);

        return webClient.post()
                .uri(analyticsUrl + "/api/analytics/summary")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(payload)
                .retrieve()
                .bodyToMono(Map.class)
                .block(java.time.Duration.ofSeconds(30));
    }
}
