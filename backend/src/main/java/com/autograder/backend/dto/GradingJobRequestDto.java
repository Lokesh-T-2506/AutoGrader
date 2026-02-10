package com.autograder.backend.dto;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GradingJobRequestDto {

    @NotNull(message = "Submission ID is required")
    private Long submissionId;
}
