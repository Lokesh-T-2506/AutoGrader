package com.autograder.backend.controller;

import com.autograder.backend.entity.Assignment;
import com.autograder.backend.repository.AssignmentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/assignments")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
@Slf4j
public class AssignmentController {

    private final AssignmentRepository assignmentRepository;

    @PostMapping
    public ResponseEntity<?> createAssignment(@RequestBody java.util.Map<String, Object> payload) {
        log.info("Received assignment creation request: {}", payload);
        try {
            Assignment assignment = new Assignment();
            assignment.setTitle((String) payload.get("title"));
            assignment.setDescription((String) payload.get("description"));

            Object points = payload.get("totalPoints");
            if (points != null) {
                assignment.setTotalPoints(((Number) points).doubleValue());
            } else {
                assignment.setTotalPoints(0.0);
            }

            assignment.setRubricText((String) payload.get("rubricText"));
            assignment.setReferenceSolutionText((String) payload.get("referenceSolutionText"));

            // Course logic removed for simplification
            Assignment saved = assignmentRepository.save(assignment);
            log.info("Assignment saved with ID: {}", saved.getId());
            return ResponseEntity.ok(saved);

        } catch (Exception e) {
            log.error("Error creating assignment", e);
            return ResponseEntity.internalServerError().body("Error: " + e.getMessage());
        }
    }

    @GetMapping
    public ResponseEntity<List<Assignment>> getAllAssignments() {
        return ResponseEntity.ok(assignmentRepository.findAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Assignment> getAssignmentById(@PathVariable Long id) {
        return assignmentRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
