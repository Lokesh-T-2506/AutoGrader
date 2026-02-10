package com.autograder.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserResponseDto {

    private Long id;
    private String email;
    private String name;
    private String role;
    private LocalDateTime createdAt;

    // Note: Password is deliberately excluded for security
}
