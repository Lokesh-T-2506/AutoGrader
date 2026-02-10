package com.autograder.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SubmissionRequestDto {

    @NotNull(message = "Assignment ID is required")
    private Long assignmentId;

    @NotNull(message = "Student ID is required")
    private Long studentId;

    @NotBlank(message = "File path is required")
    private String filePath;

    private String fileType; // pdf, jpg, png, etc.
}
