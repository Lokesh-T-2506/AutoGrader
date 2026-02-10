package com.autograder.backend.repository;

import com.autograder.backend.entity.Assignment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AssignmentRepository extends JpaRepository<Assignment, Long> {

    /**
     * Find all assignments for a specific course.
     *
     * @param courseId the course ID
     * @return list of assignments
     */
    @Query("SELECT a FROM Assignment a WHERE a.course.id = :courseId")
    List<Assignment> findByCourseId(@Param("courseId") Long courseId);

    /**
     * Find assignments with due dates before a specific date/time.
     * Useful for finding overdue or upcoming assignments.
     *
     * @param dueDate the date/time to compare against
     * @return list of assignments
     */
    List<Assignment> findByDueDateBefore(LocalDateTime dueDate);

    /**
     * Find assignments with due dates after a specific date/time.
     *
     * @param dueDate the date/time to compare against
     * @return list of assignments
     */
    List<Assignment> findByDueDateAfter(LocalDateTime dueDate);

    /**
     * Find assignments for a course with due dates between two dates.
     * Useful for filtering assignments by date range.
     *
     * @param courseId  the course ID
     * @param startDate start of date range
     * @param endDate   end of date range
     * @return list of assignments
     */
    @Query("SELECT a FROM Assignment a WHERE a.course.id = :courseId AND a.dueDate BETWEEN :startDate AND :endDate")
    List<Assignment> findByCourseIdAndDueDateBetween(
            @Param("courseId") Long courseId,
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate);
}
