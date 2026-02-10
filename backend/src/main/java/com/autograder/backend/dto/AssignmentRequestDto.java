package com.autograder.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AssignmentRequestDto {

    @NotNull(message = "Course ID is required")
    private Long courseId;

    @NotBlank(message = "Title is required")
    private String title;

    private String description;

    @NotNull(message = "Total points is required")
    private Double totalPoints;

    private String rubricJson; // JSON string containing rubric criteria

    private LocalDateTime dueDate;
}
