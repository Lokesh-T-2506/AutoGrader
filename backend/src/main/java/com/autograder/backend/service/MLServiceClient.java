package com.autograder.backend.service;

import com.autograder.backend.dto.GradingResultRequestDto;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

@Service
public class MLServiceClient {

    private final WebClient webClient;

    @Value("${ml-service.ocr.url}")
    private String ocrServiceUrl;

    @Value("${ml-service.math-parser.url}")
    private String mathParserServiceUrl;

    @Value("${ml-service.grading.url}")
    private String gradingServiceUrl;

    @Value("${ml-service.feedback.url}")
    private String feedbackServiceUrl;

    public MLServiceClient(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.build();
    }

    /**
     * Call OCR service to extract text from a file.
     */
    public Mono<String> extractText(String filePath) {
        org.springframework.util.MultiValueMap<String, Object> body = new org.springframework.util.LinkedMultiValueMap<>();
        body.add("file", new org.springframework.core.io.FileSystemResource(filePath));

        return webClient.post()
                .uri(ocrServiceUrl + "/api/ocr/extract")
                .contentType(org.springframework.http.MediaType.MULTIPART_FORM_DATA)
                .body(org.springframework.web.reactive.function.BodyInserters.fromMultipartData(body))
                .retrieve()
                .bodyToMono(Map.class)
                .map(response -> (String) response.get("text"));
    }

    /**
     * Call Grading Engine to evaluate submission using textual rubric and reference
     * solution.
     */
    public Mono<GradingResultRequestDto> evaluateSubmission(
            String studentAnswer,
            String referenceSolution,
            String rubricText) {

        Map<String, Object> request = Map.of(
                "student_answer", studentAnswer,
                "reference_solution", referenceSolution,
                "rubric_text", rubricText);

        return webClient.post()
                .uri(gradingServiceUrl + "/api/grade/evaluate")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(GradingResultRequestDto.class);
    }
}
