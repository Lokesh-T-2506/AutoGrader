package com.autograder.backend.dto;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GradingResultRequestDto {

    @NotNull(message = "Job ID is required")
    private Long jobId;

    @NotNull(message = "Score is required")
    private Double score;

    @NotNull(message = "Max score is required")
    private Double maxScore;

    private String feedbackJson; // JSON containing detailed feedback

    private Double confidenceScore; // ML model confidence (0.0 - 1.0)

    private String ocrText; // Extracted text from handwriting

    private Boolean requiresReview; // Flag for manual review

    private Long reviewedBy; // User ID of reviewer
}
