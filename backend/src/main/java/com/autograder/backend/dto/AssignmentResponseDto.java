package com.autograder.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AssignmentResponseDto {

    private Long id;
    private Long courseId;
    private String courseName;
    private String title;
    private String description;
    private Double totalPoints;
    private String rubricText;
    private String referenceSolutionPath;
    private String referenceSolutionText;
    private LocalDateTime dueDate;
    private LocalDateTime createdAt;
}
