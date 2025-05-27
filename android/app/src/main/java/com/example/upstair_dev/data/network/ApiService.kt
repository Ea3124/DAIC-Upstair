package com.example.upstair_dev.data.network

import com.example.upstair_dev.data.model.LoginRequest
import com.example.upstair_dev.data.model.LoginResponse
import com.example.upstair_dev.data.model.ScholarshipResponse
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface ApiService {
    @POST("/login")
    fun login(@Body request: LoginRequest): Call<LoginResponse>

    @GET("/documents")
    fun getScholarships(): Call<List<ScholarshipResponse>>
}
