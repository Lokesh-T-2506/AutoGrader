package com.autograder.backend.repository;

import com.autograder.backend.entity.Submission;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SubmissionRepository extends JpaRepository<Submission, Long> {

    /**
     * Find all submissions for a specific assignment.
     *
     * @param assignmentId the assignment ID
     * @return list of submissions
     */
    @Query("SELECT s FROM Submission s WHERE s.assignment.id = :assignmentId")
    List<Submission> findByAssignmentId(@Param("assignmentId") Long assignmentId);

    /**
     * Find all submissions by a specific student.
     *
     * @param studentId the student's user ID
     * @return list of submissions
     */
    @Query("SELECT s FROM Submission s WHERE s.student.id = :studentId")
    List<Submission> findByStudentId(@Param("studentId") Long studentId);

    /**
     * Find submissions by a student for a specific assignment.
     * Useful for checking if a student has already submitted.
     *
     * @param assignmentId the assignment ID
     * @param studentId    the student's user ID
     * @return list of submissions (may be multiple if resubmissions allowed)
     */
    @Query("SELECT s FROM Submission s WHERE s.assignment.id = :assignmentId AND s.student.id = :studentId")
    List<Submission> findByAssignmentIdAndStudentId(
            @Param("assignmentId") Long assignmentId,
            @Param("studentId") Long studentId);

    /**
     * Find submissions by status.
     * Useful for finding pending or failed submissions.
     *
     * @param status the submission status (PENDING, PROCESSING, GRADED, FAILED)
     * @return list of submissions
     */
    @Query("SELECT s FROM Submission s WHERE s.status = :status")
    List<Submission> findByStatus(@Param("status") Submission.SubmissionStatus status);

    /**
     * Get the most recent submission for a student on an assignment.
     *
     * @param assignmentId the assignment ID
     * @param studentId    the student's user ID
     * @return Optional containing the most recent submission if found
     */
    @Query("SELECT s FROM Submission s WHERE s.assignment.id = :assignmentId AND s.student.id = :studentId ORDER BY s.submittedAt DESC LIMIT 1")
    Optional<Submission> findLatestByAssignmentIdAndStudentId(
            @Param("assignmentId") Long assignmentId,
            @Param("studentId") Long studentId);
}
