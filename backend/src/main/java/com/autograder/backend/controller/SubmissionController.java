package com.autograder.backend.controller;

import com.autograder.backend.entity.Assignment;
import com.autograder.backend.entity.Submission;
import com.autograder.backend.entity.User;
import com.autograder.backend.repository.AssignmentRepository;
import com.autograder.backend.repository.SubmissionRepository;
import com.autograder.backend.repository.UserRepository;
import com.autograder.backend.service.GradingService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@RestController
@RequestMapping("/api/submissions")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
@Slf4j
public class SubmissionController {

    private final SubmissionRepository submissionRepository;
    private final AssignmentRepository assignmentRepository;
    private final UserRepository userRepository;
    private final GradingService gradingService;

    @Value("${file.upload-dir}")
    private String uploadDir;

    @PostMapping
    public ResponseEntity<?> createSubmission(
            @RequestParam("file") MultipartFile file,
            @RequestParam("assignmentId") Long assignmentId,
            @RequestParam("studentId") Long studentId) {

        log.info("Received submission upload for assignment: {}, student: {}", assignmentId, studentId);

        try {
            Assignment assignment = assignmentRepository.findById(assignmentId)
                    .orElseThrow(() -> new RuntimeException("Assignment not found"));
            User student = userRepository.findById(studentId)
                    .orElseThrow(() -> new RuntimeException("Student not found"));

            // Ensure upload directory exists
            Path uploadPath = Paths.get(uploadDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            // Save file
            String fileName = UUID.randomUUID() + "_" + file.getOriginalFilename();
            Path filePath = uploadPath.resolve(fileName);
            Files.copy(file.getInputStream(), filePath);

            // Create Submission entity
            Submission submission = new Submission();
            submission.setAssignment(assignment);
            submission.setStudent(student);
            submission.setFilePath(filePath.toAbsolutePath().toString());

            Submission saved = submissionRepository.save(submission);
            log.info("Submission saved with ID: {}", saved.getId());

            // Trigger Grading
            gradingService.startGrading(saved.getId());

            return ResponseEntity.ok(saved);

        } catch (IOException e) {
            log.error("Failed to store file", e);
            return ResponseEntity.internalServerError().body("Failed to store file: " + e.getMessage());
        } catch (Exception e) {
            log.error("Error creating submission", e);
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
        }
    }
}
