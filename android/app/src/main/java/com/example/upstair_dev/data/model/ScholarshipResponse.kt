package com.example.upstair_dev.data.model

data class ScholarshipResponse(
    val id: Int,
    val title: String,
    val link: String,
    val gpa: Double,
    val start_date: String,
    val end_date: String,
    val status: String,
    val grade: Int
)