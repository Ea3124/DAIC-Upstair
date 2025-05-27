package com.example.upstair_dev.login

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.upstair_dev.R
import com.example.upstair_dev.data.model.LoginRequest
import com.example.upstair_dev.data.model.LoginResponse
import com.example.upstair_dev.data.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class LoginActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            LoginScreen()
        }
    }
}

@Composable
fun LoginScreen() {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var resultText by remember { mutableStateOf("") }

    val gradient = Brush.verticalGradient(colors = listOf(Color(0xFF143C8A), Color(0xFF143C8A)))

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(brush = gradient),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .padding(24.dp)
                .background(Color.White, shape = RoundedCornerShape(24.dp))
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(72.dp)
                    .background(Color(0xFFFFC100), shape = RoundedCornerShape(36.dp))
            ) {
                Image(
                    painter = painterResource(id = R.drawable.ic_bot),
                    contentDescription = "Bot Icon",
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
            }

            Spacer(modifier = Modifier.height(16.dp))
            Text("SearCh", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color(0xFF143C8A))
            Text("개인 맞춤형 장학금 알리미", fontSize = 14.sp, color = Color.Gray)

            Spacer(modifier = Modifier.height(24.dp))

            OutlinedTextField(
                value = email,
                onValueChange = { email = it },
                label = { Text("아이디") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            )

            Spacer(modifier = Modifier.height(16.dp))

            OutlinedTextField(
                value = password,
                onValueChange = { password = it },
                label = { Text("비밀번호") },
                visualTransformation = PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            )

            Spacer(modifier = Modifier.height(24.dp))

            TextButton(
                onClick = {
                    val loginRequest = LoginRequest(email, password)
                    RetrofitClient.apiService.login(loginRequest)
                        .enqueue(object : Callback<LoginResponse> {
                            override fun onResponse(
                                call: Call<LoginResponse>,
                                response: Response<LoginResponse>
                            ) {
                                resultText = if (response.isSuccessful) {
                                    val name = response.body()?.name ?: "알 수 없음"
                                    Log.d("API", "로그인 성공: $name")
                                    "환영합니다, $name"
                                } else {
                                    Log.e("API", "로그인 실패: ${response.code()}")
                                    "로그인 실패: ${response.code()}"
                                }
                            }

                            override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                                Log.e("API", "네트워크 오류: ${t.message}")
                                resultText = "네트워크 오류: ${t.message}"
                            }
                        })
                }
            ) {
                Text("로그인", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color(0xFF143C8A))
            }

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
                modifier = Modifier.fillMaxWidth()
            ) {
                TextButton(onClick = { /* 회원가입 이동 */ }) {
                    Text("회원가입", fontSize = 14.sp, color = Color(0xFF143C8A))
                }

                Box(
                    modifier = Modifier
                        .height(16.dp)
                        .width(1.dp)
                        .background(Color.LightGray)
                )

                TextButton(onClick = { /* 비밀번호 찾기 이동 */ }) {
                    Text("비밀번호 찾기", fontSize = 14.sp, color = Color(0xFF143C8A))
                }
            }


            Spacer(modifier = Modifier.height(12.dp))
            Text(resultText)
        }
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun LoginScreenPreview() {
    LoginScreen()
}