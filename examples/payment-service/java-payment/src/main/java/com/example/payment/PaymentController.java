package com.example.payment;

import com.example.errors.PaymentDeclinedException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class PaymentController {

    @PostMapping("/payments")
    public Map<String, String> createPayment() {
        throw new PaymentDeclinedException();
    }

    @ExceptionHandler(PaymentDeclinedException.class)
    public ResponseEntity<Map<String, Object>> handlePaymentDeclined(PaymentDeclinedException error) {
        return ResponseEntity.status(PaymentDeclinedException.HTTP_STATUS).body(Map.of(
                "code", PaymentDeclinedException.CODE,
                "message", error.getMessage(),
                "retryable", PaymentDeclinedException.RETRYABLE
        ));
    }
}
