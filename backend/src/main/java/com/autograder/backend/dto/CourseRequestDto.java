package com.autograder.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CourseRequestDto {

    @NotBlank(message = "Course name is required")
    private String name;

    private String description;

    @NotNull(message = "Instructor ID is required")
    private Long instructorId;
}
