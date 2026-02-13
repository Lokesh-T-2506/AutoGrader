package com.autograder.backend.controller;

import com.autograder.backend.service.GradingService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/grading")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class GradingController {

    private final GradingService gradingService;

    @PostMapping("/jobs")
    public ResponseEntity<?> createGradingJob(@RequestBody com.autograder.backend.dto.GradingJobRequestDto request) {
        gradingService.startGrading(request.getSubmissionId());

        Map<String, Object> response = new HashMap<>();
        response.put("message", "Grading process started");
        response.put("submissionId", request.getSubmissionId());
        response.put("status", "PROCESSING");

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
