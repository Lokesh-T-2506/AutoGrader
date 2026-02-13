package com.autograder.backend.service;

import com.autograder.backend.entity.*;
import com.autograder.backend.repository.*;
import com.autograder.backend.dto.GradingResultRequestDto;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
@Slf4j
public class GradingService {

    private final MLServiceClient mlServiceClient;
    private final SubmissionRepository submissionRepository;
    private final GradingJobRepository gradingJobRepository;
    private final GradingResultRepository gradingResultRepository;

    @Transactional
    public void startGrading(Long submissionId) {
        Submission submission = submissionRepository.findById(submissionId)
                .orElseThrow(() -> new RuntimeException("Submission not found"));

        // Create Grading Job
        GradingJob job = new GradingJob();
        job.setSubmission(submission);
        job.setStatus(GradingJob.JobStatus.PROCESSING);
        job.setStartedAt(LocalDateTime.now());
        GradingJob savedJob = gradingJobRepository.save(job);

        // Chain the ML calls
        Assignment assignment = submission.getAssignment();

        mlServiceClient.extractText(submission.getFilePath())
                .flatMap(studentText -> mlServiceClient.evaluateSubmission(
                        studentText,
                        assignment.getReferenceSolutionText(),
                        assignment.getRubricText()).map(resultDto -> {
                            saveGradingResult(savedJob, resultDto, studentText);
                            return resultDto;
                        }))
                .subscribe(
                        success -> log.info("Grading completed for submission: {}", submissionId),
                        error -> handleGradingError(savedJob, error));
    }

    private void saveGradingResult(GradingJob job, GradingResultRequestDto dto, String studentText) {
        GradingResult result = new GradingResult();
        result.setJob(job);
        result.setScore(dto.getScore());
        result.setMaxScore(dto.getMaxScore());
        result.setFeedbackJson(dto.getFeedbackJson());
        result.setConfidenceScore(dto.getConfidenceScore());
        result.setOcrText(studentText);
        result.setRequiresReview(dto.getRequiresReview());
        gradingResultRepository.save(result);

        job.setStatus(GradingJob.JobStatus.COMPLETED);
        job.setCompletedAt(LocalDateTime.now());
        gradingJobRepository.save(job);

        Submission submission = job.getSubmission();
        submission.setStatus(Submission.SubmissionStatus.GRADED);
        submissionRepository.save(submission);
    }

    private void handleGradingError(GradingJob job, Throwable error) {
        log.error("Grading failed for job: {}", job.getId(), error);
        job.setStatus(GradingJob.JobStatus.FAILED);
        job.setErrorMessage(error.getMessage());
        job.setCompletedAt(LocalDateTime.now());
        gradingJobRepository.save(job);

        Submission submission = job.getSubmission();
        submission.setStatus(Submission.SubmissionStatus.FAILED);
        submissionRepository.save(submission);
    }
}
