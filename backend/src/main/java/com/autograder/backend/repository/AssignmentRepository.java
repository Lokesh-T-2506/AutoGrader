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
}
