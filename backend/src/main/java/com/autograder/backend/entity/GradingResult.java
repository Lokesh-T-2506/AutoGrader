package com.autograder.backend.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "grading_results")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class GradingResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "job_id", nullable = false)
    private GradingJob job;

    @Column(nullable = false)
    private Double score;

    @Column(name = "max_score", nullable = false)
    private Double maxScore;

    @Column(name = "feedback_json", columnDefinition = "TEXT")
    private String feedbackJson; // JSON containing detailed feedback per rubric item

    @Column(name = "confidence_score")
    private Double confidenceScore; // ML model confidence (0.0 - 1.0)

    @Column(name = "ocr_text", columnDefinition = "TEXT")
    private String ocrText; // Extracted text from handwriting

    @Column(name = "requires_review")
    private Boolean requiresReview; // Flag for manual review

    @Column(name = "reviewed_by")
    private Long reviewedBy; // User ID of reviewer

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (requiresReview == null) {
            requiresReview = false;
        }
    }
}
