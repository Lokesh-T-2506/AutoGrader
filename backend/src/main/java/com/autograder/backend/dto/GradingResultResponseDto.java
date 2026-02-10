package com.autograder.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GradingResultResponseDto {

    private Long id;
    private Long jobId;
    private Double score;
    private Double maxScore;
    private String feedbackJson;
    private Double confidenceScore;
    private String ocrText;
    private Boolean requiresReview;
    private Long reviewedBy;
    private String reviewerName;
    private LocalDateTime createdAt;
}
