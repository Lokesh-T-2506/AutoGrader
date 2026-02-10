package com.autograder.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/submissions")
@CrossOrigin(origins = "*")
public class SubmissionController {

    @PostMapping("/upload")
    public ResponseEntity<?> uploadSubmission(
            @RequestParam("file") MultipartFile file,
            @RequestParam("assignmentId") Long assignmentId,
            @RequestParam("studentId") Long studentId) {

        // TODO: Implement file upload logic
        Map<String, Object> response = new HashMap<>();
        response.put("message", "File upload endpoint - implementation pending");
        response.put("fileName", file.getOriginalFilename());
        response.put("fileSize", file.getSize());
        response.put("assignmentId", assignmentId);
        response.put("studentId", studentId);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getSubmission(@PathVariable Long id) {
        // TODO: Implement get submission logic
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Get submission endpoint - implementation pending");
        response.put("submissionId", id);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/assignment/{assignmentId}")
    public ResponseEntity<?> getSubmissionsByAssignment(@PathVariable Long assignmentId) {
        // TODO: Implement get submissions by assignment
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Get submissions by assignment - implementation pending");
        response.put("assignmentId", assignmentId);

        return ResponseEntity.ok(response);
    }
}
