package com.autograder.backend.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "assignments")
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonIgnoreProperties({ "hibernateLazyInitializer", "handler" })
public class Assignment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Course relationship removed for simplification
    // @ManyToOne(fetch = FetchType.LAZY)
    // @JoinColumn(name = "course_id", nullable = false)
    // private Course course;

    @Column(nullable = false)
    private String title;

    @Column(length = 2000)
    private String description;

    @Column(name = "total_points", nullable = false)
    private Double totalPoints;

    @Column(name = "rubric_text", columnDefinition = "TEXT")
    private String rubricText; // Natural language grading instructions

    @Column(name = "reference_solution_path")
    private String referenceSolutionPath; // Path to instructor's solved PDF/image

    @Column(name = "reference_solution_text", columnDefinition = "TEXT")
    private String referenceSolutionText; // OCR-extracted text from reference solution

    @Column(name = "due_date")
    private LocalDateTime dueDate;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
