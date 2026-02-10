package com.autograder.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/grading")
@CrossOrigin(origins = "*")
public class GradingController {

    @PostMapping("/jobs")
    public ResponseEntity<?> createGradingJob(@RequestBody Map<String, Object> request) {
        // TODO: Implement grading job creation
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Create grading job endpoint - implementation pending");
        response.put("submissionId", request.get("submissionId"));
        response.put("jobId", 1L); // Placeholder
        response.put("status", "PENDING");

        return ResponseEntity.ok(response);
    }

    @GetMapping("/jobs/{jobId}")
    public ResponseEntity<?> getJobStatus(@PathVariable Long jobId) {
        // TODO: Implement job status retrieval
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Get job status endpoint - implementation pending");
        response.put("jobId", jobId);
        response.put("status", "PENDING");

        return ResponseEntity.ok(response);
    }

    @GetMapping("/results/{jobId}")
    public ResponseEntity<?> getGradingResult(@PathVariable Long jobId) {
        // TODO: Implement result retrieval
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Get grading result endpoint - implementation pending");
        response.put("jobId", jobId);

        return ResponseEntity.ok(response);
    }
}
