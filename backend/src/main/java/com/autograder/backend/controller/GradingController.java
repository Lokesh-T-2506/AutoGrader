package com.autograder.backend.controller;

import com.autograder.backend.dto.GradingJobRequestDto;
import com.autograder.backend.repository.GradingJobRepository;
import com.autograder.backend.repository.GradingResultRepository;
import com.autograder.backend.service.GradingService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/grading")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class GradingController {

    private final GradingService gradingService;
    private final GradingJobRepository gradingJobRepository;
    private final GradingResultRepository gradingResultRepository;

    @PostMapping("/jobs")
    public ResponseEntity<?> createGradingJob(@RequestBody GradingJobRequestDto request) {
        gradingService.startGrading(request.getSubmissionId());

        Map<String, Object> response = new HashMap<>();
        response.put("message", "Grading process started");
        response.put("submissionId", request.getSubmissionId());
        response.put("status", "PROCESSING");

        return ResponseEntity.ok(response);
    }

    @GetMapping("/jobs/{jobId}")
    public ResponseEntity<?> getJobStatus(@PathVariable Long jobId) {
        return gradingJobRepository.findById(jobId)
                .map(job -> {
                    com.autograder.backend.dto.GradingJobResponseDto dto = new com.autograder.backend.dto.GradingJobResponseDto();
                    dto.setId(job.getId());
                    dto.setSubmissionId(job.getSubmission().getId());
                    dto.setStatus(job.getStatus().name());
                    dto.setErrorMessage(job.getErrorMessage());
                    dto.setCreatedAt(job.getCreatedAt());
                    dto.setStartedAt(job.getStartedAt());
                    dto.setCompletedAt(job.getCompletedAt());
                    return ResponseEntity.ok(dto);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/results/{jobId}")
    public ResponseEntity<?> getGradingResult(@PathVariable Long jobId) {
        return gradingResultRepository.findByJobId(jobId)
                .map(result -> {
                    com.autograder.backend.dto.GradingResultResponseDto dto = new com.autograder.backend.dto.GradingResultResponseDto();
                    dto.setId(result.getId());
                    dto.setJobId(result.getJob().getId());
                    dto.setScore(result.getScore());
                    dto.setMaxScore(result.getMaxScore());
                    dto.setFeedbackJson(result.getFeedbackJson());
                    dto.setConfidenceScore(result.getConfidenceScore());
                    dto.setOcrText(result.getOcrText());
                    dto.setRequiresReview(result.getRequiresReview());
                    dto.setCreatedAt(result.getCreatedAt());
                    return ResponseEntity.ok(dto);
                })
                .orElse(ResponseEntity.notFound().build());
    }
}
