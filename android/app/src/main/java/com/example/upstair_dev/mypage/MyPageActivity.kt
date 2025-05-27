package com.example.upstair_dev.mypage

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class MyPageActivity : ComponentActivity() {
    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyPageScreen(
                onBackClick = { finish() },
                onSave = { gpa, status, year ->
                    // 여기서 API 호출 또는 SharedPreferences 저장 가능
                    Log.d("MyPage", "저장됨 - 학점: $gpa, 학적: $status, 학년: $year")
                }
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyPageScreen(
    onBackClick: () -> Unit,
    onSave: (String, String, String) -> Unit
) {
    var gpa by remember { mutableStateOf("3.5") }
    var status by remember { mutableStateOf("재학생") }
    var year by remember { mutableStateOf("3학년") }

    val statusOptions = listOf("재학생", "휴학생")
    val yearOptions = listOf("1학년", "2학년", "3학년", "4학년")

    Column(modifier = Modifier
        .fillMaxSize()
        .background(Color(0xFFF9F9F9))) {

        TopAppBar(
            title = {
                Text("내 정보", color = Color.White, fontWeight = FontWeight.Bold)
            },
            navigationIcon = {
                IconButton(onClick = onBackClick) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "뒤로가기", tint = Color.White)
                }
            },
            actions = {
                Button(
                    onClick = { onSave(gpa, status, year) },
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.width(74.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFFC100))
                ) {
                    Text("수정", color = Color.Black, fontWeight = FontWeight.Bold)
                }
                Spacer(modifier = Modifier.width(8.dp))
            },
            colors = TopAppBarDefaults.topAppBarColors(containerColor = Color(0xFF143C8A))
        )

        Column(modifier = Modifier.padding(24.dp)) {
        
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .shadow(4.dp, RoundedCornerShape(16.dp))
                    .background(Color.White, RoundedCornerShape(16.dp))
                    .padding(24.dp)
            ) {
                Column {

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Box(
                            modifier = Modifier
                                .size(72.dp)
                                .background(Color(0xFFFFC100), RoundedCornerShape(36.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Person,
                                contentDescription = null,
                                tint = Color.Black,
                                modifier = Modifier.size(40.dp)
                            )
                        }

                        Spacer(modifier = Modifier.width(16.dp))

                        Column {
                            Text("홍길동", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF143C8A))
                            Text("정보컴퓨터공학부", fontSize = 14.sp, color = Color.Gray)
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Text(
                        "학점 (최대 4.5)",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color(0xFF666666)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = gpa,
                        onValueChange = { gpa = it },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(50.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = TextFieldDefaults.outlinedTextFieldColors(
                            containerColor = Color(0xFFF5F5F5),
                            unfocusedBorderColor = Color(0xFFCCCCCC),
                            focusedBorderColor = Color(0xFF143C8A)
                        ),
                        singleLine = true
                    )


                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        "학적 구분",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color(0xFF666666)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    DropdownMenuBox(options = statusOptions, selected = status, onSelected = { status = it })

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        "학년",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color(0xFF666666)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    DropdownMenuBox(options = yearOptions, selected = year, onSelected = { year = it })
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .shadow(4.dp, RoundedCornerShape(16.dp))
                    .background(Color.White, RoundedCornerShape(16.dp))
                    .padding(24.dp)
            ) {
                Column {
                    Text(
                        "기타 설정",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF143C8A)
                    )

                    Spacer(modifier = Modifier.height(20.dp))

                    Column(modifier = Modifier.padding(start = 8.dp)) {
                        Text("알림 설정", fontSize = 12.sp, color = Color.Black)
                        Spacer(modifier = Modifier.height(16.dp))

                        Text("개인정보 처리방침", fontSize = 12.sp, color = Color.Black)
                        Spacer(modifier = Modifier.height(16.dp))

                        Text("로그아웃", fontSize = 12.sp, color = Color.Red)
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DropdownMenuBox(
    options: List<String>,
    selected: String,
    onSelected: (String) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = !expanded },
        modifier = Modifier.fillMaxWidth()
    ) {
        OutlinedTextField(
            value = selected,
            onValueChange = {},
            readOnly = true,
            trailingIcon = {
                ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded)
            },
            modifier = Modifier
                .menuAnchor()
                .fillMaxWidth()
                .height(50.dp),
            shape = RoundedCornerShape(12.dp),
            singleLine = true,
            colors = TextFieldDefaults.outlinedTextFieldColors(
                containerColor = Color(0xFFF5F5F5),
                unfocusedBorderColor = Color(0xFFCCCCCC),
                focusedBorderColor = Color(0xFF143C8A)
            )
        )

        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false },
            modifier = Modifier.background(Color.White)
        ) {
            options.forEach { option ->
                DropdownMenuItem(
                    text = { Text(option) },
                    onClick = {
                        onSelected(option)
                        expanded = false
                    }
                )
            }
        }
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun PreviewMyPageScreen() {
    MyPageScreen(
        onBackClick = {},
        onSave = { gpa, status, year ->
            // 테스트용 프리뷰: 저장된 값 로그 출력 없이 무시
        }
    )
}

