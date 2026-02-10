package com.autograder.backend.repository;

import com.autograder.backend.entity.Course;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CourseRepository extends JpaRepository<Course, Long> {

    /**
     * Find all courses taught by a specific instructor.
     *
     * @param instructorId the instructor's user ID
     * @return list of courses
     */
    @Query("SELECT c FROM Course c WHERE c.instructor.id = :instructorId")
    List<Course> findByInstructorId(@Param("instructorId") Long instructorId);

    /**
     * Find courses by name (case-insensitive partial match).
     * Useful for search functionality.
     *
     * @param name the course name to search for
     * @return list of matching courses
     */
    List<Course> findByNameContainingIgnoreCase(String name);
}
