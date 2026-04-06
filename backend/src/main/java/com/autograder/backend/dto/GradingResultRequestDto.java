package com.autograder.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonAlias;
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
    @JsonProperty("total_score")
    @JsonAlias("score")
    private Double score;

    @NotNull(message = "Max score is required")
    @JsonProperty("max_score")
    @JsonAlias("maxScore")
    private Double maxScore;

    @JsonProperty("feedback_json")
    private String feedbackJson; // JSON containing detailed feedback

    @JsonProperty("overall_confidence")
    @JsonAlias("confidenceScore")
    private Double confidenceScore; // ML model confidence (0.0 - 1.0)

    @JsonProperty("ocr_text")
    private String ocrText; // Extracted text from handwriting

    @JsonProperty("requires_review")
    private Boolean requiresReview; // Flag for manual review

    @JsonProperty("reviewed_by")
    private Long reviewedBy; // User ID of reviewer
}
