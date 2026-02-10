package com.autograder.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CourseResponseDto {

    private Long id;
    private String name;
    private String description;
    private Long instructorId;
    private String instructorName;
    private LocalDateTime createdAt;
}
