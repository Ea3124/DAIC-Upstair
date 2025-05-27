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
    val link: String,
    val isFiltered: Boolean = false
)

data class FilteredScholarshipResponse(
    val notice_title: String?,
    val url: String?
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

    fun fetchFilteredScholarships(minGpa: Double, grade: Int, status: String) {
        RetrofitClient.apiService.getFilteredScholarships(minGpa, grade, status)
            .enqueue(object : Callback<List<FilteredScholarshipResponse>> {
                override fun onResponse(
                    call: Call<List<FilteredScholarshipResponse>>,
                    response: Response<List<FilteredScholarshipResponse>>
                ) {
                    if (response.isSuccessful) {
                        val body = response.body() ?: emptyList()

                        _scholarships.value = body.map {
                            Scholarship(
                                name = it.notice_title ?: "제목 없음",
                                deadline = "정보 없음", // 해당 API에는 날짜 정보 없음
                                status = "모집중",     // 서버 응답에는 상태 없음 → 기본값 지정
                                link = it.url ?: "",     // null 방어
                                isFiltered = true
                            )
                        }
                    } else {
                        Log.e("FilterAPI", "응답 실패: ${response.code()}")
                    }
                }

                override fun onFailure(call: Call<List<FilteredScholarshipResponse>>, t: Throwable) {
                    Log.e("FilterAPI", "네트워크 오류", t)
                }
            })
    }

    fun fetchAskedScholarships(question: String) {
        val body = mapOf("question" to question)

        RetrofitClient.apiService.askDatabase(body)
            .enqueue(object : Callback<List<FilteredScholarshipResponse>> {
                override fun onResponse(
                    call: Call<List<FilteredScholarshipResponse>>,
                    response: Response<List<FilteredScholarshipResponse>>
                ) {
                    if (response.isSuccessful) {
                        val list = response.body() ?: emptyList()
                        _scholarships.value = list.map {
                            Scholarship(
                                name = it.notice_title ?: "제목 없음",
                                deadline = "",   // ❌ 표시 안 함
                                status = "",     // ❌ 표시 안 함
                                link = it.url ?: ""
                            )
                        }
                    } else {
                        Log.e("AskAPI", "응답 실패: ${response.code()}")
                    }
                }

                override fun onFailure(call: Call<List<FilteredScholarshipResponse>>, t: Throwable) {
                    Log.e("AskAPI", "네트워크 오류", t)
                }
            })
    }

}