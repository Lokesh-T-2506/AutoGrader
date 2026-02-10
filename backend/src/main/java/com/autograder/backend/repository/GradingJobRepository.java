package com.autograder.backend.repository;

import com.autograder.backend.entity.GradingJob;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GradingJobRepository extends JpaRepository<GradingJob, Long> {

    /**
     * Find the grading job for a specific submission.
     * Since there's a one-to-one relationship, there should be at most one job.
     *
     * @param submissionId the submission ID
     * @return Optional containing the grading job if found
     */
    @Query("SELECT gj FROM GradingJob gj WHERE gj.submission.id = :submissionId")
    Optional<GradingJob> findBySubmissionId(@Param("submissionId") Long submissionId);

    /**
     * Find grading jobs by status.
     * Useful for processing pending jobs or monitoring failed jobs.
     *
     * @param status the job status (PENDING, PROCESSING, COMPLETED, FAILED)
     * @return list of grading jobs
     */
    @Query("SELECT gj FROM GradingJob gj WHERE gj.status = :status")
    List<GradingJob> findByStatus(@Param("status") GradingJob.JobStatus status);

    /**
     * Find all pending jobs ordered by creation time (oldest first).
     * Useful for job queue processing.
     *
     * @return list of pending jobs
     */
    @Query("SELECT gj FROM GradingJob gj WHERE gj.status = 'PENDING' ORDER BY gj.createdAt ASC")
    List<GradingJob> findPendingJobsOrderByCreatedAt();

    /**
     * Count jobs by status.
     * Useful for monitoring system health.
     *
     * @param status the job status
     * @return count of jobs with that status
     */
    @Query("SELECT COUNT(gj) FROM GradingJob gj WHERE gj.status = :status")
    long countByStatus(@Param("status") GradingJob.JobStatus status);
}
