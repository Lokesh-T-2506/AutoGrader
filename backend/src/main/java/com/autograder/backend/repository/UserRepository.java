package com.autograder.backend.repository;

import com.autograder.backend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * Find a user by their email address.
     * Useful for login and checking if email already exists.
     *
     * @param email the user's email
     * @return Optional containing the user if found
     */
    Optional<User> findByEmail(String email);

    /**
     * Check if a user with the given email exists.
     * Useful for registration validation.
     *
     * @param email the email to check
     * @return true if user exists, false otherwise
     */
    boolean existsByEmail(String email);
}
