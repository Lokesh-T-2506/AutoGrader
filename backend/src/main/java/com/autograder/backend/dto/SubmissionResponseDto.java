package com.autograder.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SubmissionResponseDto {

    private Long id;
    private Long assignmentId;
    private String assignmentTitle;
    private Long studentId;
    private String studentName;
    private String filePath;
    private String fileType;
    private String status; // PENDING, PROCESSING, GRADED, FAILED
    private LocalDateTime submittedAt;
}
