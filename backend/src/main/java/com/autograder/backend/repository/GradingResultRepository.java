package com.autograder.backend.repository;

import com.autograder.backend.entity.GradingResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GradingResultRepository extends JpaRepository<GradingResult, Long> {

    /**
     * Find the grading result for a specific grading job.
     * Since there's a one-to-one relationship, there should be at most one result.
     *
     * @param jobId the grading job ID
     * @return Optional containing the grading result if found
     */
    @Query("SELECT gr FROM GradingResult gr WHERE gr.job.id = :jobId")
    Optional<GradingResult> findByJobId(@Param("jobId") Long jobId);

    /**
     * Find all results that require manual review.
     * Useful for instructors to review low-confidence grades.
     *
     * @return list of results requiring review
     */
    @Query("SELECT gr FROM GradingResult gr WHERE gr.requiresReview = true")
    List<GradingResult> findResultsRequiringReview();

    /**
     * Find results with confidence score below a threshold.
     * Useful for identifying potentially problematic gradings.
     *
     * @param confidenceThreshold the minimum confidence score
     * @return list of results below the threshold
     */
    @Query("SELECT gr FROM GradingResult gr WHERE gr.confidenceScore < :confidenceThreshold")
    List<GradingResult> findByConfidenceScoreLessThan(@Param("confidenceThreshold") Double confidenceThreshold);

    /**
     * Find results reviewed by a specific user.
     *
     * @param reviewerId the reviewer's user ID
     * @return list of results reviewed by that user
     */
    @Query("SELECT gr FROM GradingResult gr WHERE gr.reviewedBy = :reviewerId")
    List<GradingResult> findByReviewedBy(@Param("reviewerId") Long reviewerId);

    /**
     * Get statistics for an assignment: average score, min, max.
     * Note: This returns a custom projection.
     *
     * @param assignmentId the assignment ID
     * @return list of results for that assignment
     */
    @Query("SELECT gr FROM GradingResult gr " +
            "JOIN gr.job gj " +
            "JOIN gj.submission s " +
            "WHERE s.assignment.id = :assignmentId")
    List<GradingResult> findResultsByAssignmentId(@Param("assignmentId") Long assignmentId);
}
