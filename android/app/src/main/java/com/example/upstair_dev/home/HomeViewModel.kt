package com.example.upstair_dev.home

import android.util.Log
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.compose.runtime.State
import com.example.upstair_dev.data.model.ScholarshipResponse
import com.example.upstair_dev.data.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.time.LocalDate

data class Scholarship(
    val name: String,
    val deadline: String,
    val status: String,
    val link: String
)

class HomeViewModel : ViewModel() {
    private val _scholarships = mutableStateOf<List<Scholarship>>(emptyList())
    val scholarships: State<List<Scholarship>> = _scholarships

    init {
        fetchScholarships()
    }

    private fun fetchScholarships() {
        RetrofitClient.apiService.getScholarships().enqueue(object : Callback<List<ScholarshipResponse>> {
            override fun onResponse(
                call: Call<List<ScholarshipResponse>>,
                response: Response<List<ScholarshipResponse>>
            ) {
                if (response.isSuccessful) {
                    val body = response.body() ?: emptyList()
                    val now = LocalDate.now()

                    _scholarships.value = body.map {
                        val rawStart = it.start_date?.trim()
                        val rawEnd = it.end_date?.trim()

                        val startDate = try {
                            if (!rawStart.isNullOrEmpty()) LocalDate.parse(rawStart) else LocalDate.MAX
                        } catch (e: Exception) {
                            Log.e("Scholarship", "Invalid start date: $rawStart")
                            LocalDate.MAX
                        }

                        val endDate = try {
                            if (!rawEnd.isNullOrEmpty()) LocalDate.parse(rawEnd) else LocalDate.MIN
                        } catch (e: Exception) {
                            Log.e("Scholarship", "Invalid end date: $rawEnd")
                            LocalDate.MIN
                        }

                        val status = when {
                            now.isBefore(startDate) -> "모집전"
                            now.isAfter(endDate) -> "모집완료"
                            else -> "모집중"
                        }

                        Log.d("ScholarshipDebug", "Title: ${it.title}, status: $status")

                        Scholarship(
                            name = it.title ?: "제목 없음",
                            deadline = it.end_date ?: "미정",
                            status = status,
                            link = it.link ?: ""
                        )
                    }
                }
            }

            override fun onFailure(call: Call<List<ScholarshipResponse>>, t: Throwable) {
                Log.e("Scholarship", "API Error", t)
            }
        })
    }

}