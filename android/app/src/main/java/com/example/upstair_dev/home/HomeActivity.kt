package com.example.upstair_dev.home

import android.content.Intent
import androidx.compose.ui.platform.LocalContext
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.upstair_dev.R
import com.example.upstair_dev.mypage.MyPageActivity
import com.example.upstair_dev.noti.NotiActivity

class HomeActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            HomeScreen()
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen() {
    val viewModel: HomeViewModel = viewModel()
    val scholarships by viewModel.scholarships
    val context = LocalContext.current
    var showFilter by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("SearCh", color = Color.White) },
                colors = androidx.compose.material3.TopAppBarDefaults.topAppBarColors(
                    containerColor = Color(0xFF1D3A8A)
                ),
                actions = {
                    IconButton(onClick = {
                        val intent = Intent(context, NotiActivity::class.java)
                        context.startActivity(intent)
                    }) {
                        BadgedBox(
                            badge = {
                                Badge(
                                    containerColor = Color(0xFFFFC107), // 노란색
                                ) {
                                    Text("2", fontSize = 10.sp, color = Color.Black)
                                }
                            }
                        ) {
                            Icon(
                                Icons.Default.Notifications,
                                contentDescription = "Notifications",
                                tint = Color.White
                            )
                        }
                    }
                    IconButton(onClick = {
                        val intent = Intent(context, MyPageActivity::class.java)
                        context.startActivity(intent)
                    }) {
                        Icon(
                            Icons.Default.Person,
                            contentDescription = "Profile",
                            tint = Color.White
                        )
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .background(Color(0xFFF9FAFB))
        ) {
            Spacer(modifier = Modifier.height(16.dp))

            // 검색창
            var searchText by remember { mutableStateOf("") }
            // Row 높이 고정은 하지 않고 각 요소 내부 높이 정리
            Box(
                modifier = Modifier
                    .padding(horizontal = 16.dp)
                    .fillMaxWidth()
                    .background(Color.White, shape = RoundedCornerShape(12.dp))
                    .border(1.dp, Color(0xFFE0E0E0), RoundedCornerShape(12.dp))
                    .padding(horizontal = 12.dp, vertical = 8.dp) // 텍스트 필드에 충분한 여백 제공
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.robot),
                        contentDescription = "Chatbot",
                        modifier = Modifier.size(40.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))

                    OutlinedTextField(
                        value = searchText,
                        onValueChange = { searchText = it },
                        placeholder = {
                            Text(
                                text = "어떤 장학금을 찾고 계신가요?",
                                fontSize = 14.sp,
                                color = Color.Gray
                            )
                        },
                        modifier = Modifier
                            .weight(1f)
                            .padding(horizontal = 8.dp)
                            .height(56.dp), // 필수: 기본 높이 제약 제거
                        shape = RoundedCornerShape(18.dp),
                        singleLine = true,
                        textStyle = androidx.compose.ui.text.TextStyle( // ✅ 텍스트 높이 줄이기
                            fontSize = 12.sp,
                            lineHeight = 14.sp
                        ),
                        colors = androidx.compose.material3.TextFieldDefaults.outlinedTextFieldColors(
                            containerColor = Color.White,
                            unfocusedBorderColor = Color(0xFFE0E0E0),
                            focusedBorderColor = Color(0xFF1D3A8A),
                            cursorColor = Color(0xFF1D3A8A)
                        )
                    )


                    Spacer(modifier = Modifier.width(8.dp))

                    Box(
                        modifier = Modifier
                            .size(40.dp) // Send 버튼 크기
                            .clip(RoundedCornerShape(8.dp))
                            .background(Color(0xFF1D3A8A))
                            .clickable { },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            painter = painterResource(id = R.drawable.ic_send),
                            contentDescription = "Send",
                            tint = Color.White,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // 추천 장학금 헤더
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "추천 장학금",
                    fontWeight = FontWeight.Bold,
                    fontSize = 18.sp,
                    color = Color(0xFF1D3A8A) // 남색
                )

                // 기존 IconButton → Box로 대체
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp)) // 둥근 테두리
                        .background(Color.White) // 흰색 배경
                        .border(1.dp, Color(0xFFE0E0E0), RoundedCornerShape(8.dp)) // 회색 테두리
                        .clickable { showFilter = true }
                        .padding(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            painter = painterResource(id = R.drawable.filter),
                            contentDescription = "Filter",
                            tint = Color.Black,
                            modifier = Modifier.size(15.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("필터", color = Color.Black, fontSize = 12.sp)
                    }
                }

            }

            // 장학금 리스트
            LazyColumn(contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)) {
                items(scholarships) { scholarship ->
                    ScholarshipCard(scholarship)
                }
            }

            if (showFilter) {
                AlertDialog(
                    onDismissRequest = { showFilter = false },
                    containerColor = Color.White,
                    title = { Text("필터 설정", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = Color(0xFF1D3A8A)) },
                    text = {
                        var grade by remember { mutableStateOf("") }
                        var statusExpanded by remember { mutableStateOf(false) }
                        var yearExpanded by remember { mutableStateOf(false) }
                        var selectedStatus by remember { mutableStateOf("재학") }
                        var selectedYear by remember { mutableStateOf("1학년") }

                        Column(modifier = Modifier.padding(top = 8.dp)) {
                            OutlinedTextField(
                                value = grade,
                                onValueChange = { grade = it },
                                label = { Text("학점 (최대 4.5)") },
                                placeholder = { Text("예: 3.5") },
                                shape = RoundedCornerShape(12.dp),
                                colors = androidx.compose.material3.TextFieldDefaults.outlinedTextFieldColors(
                                    unfocusedBorderColor = Color(0xFFE0E0E0),
                                    focusedBorderColor = Color(0xFF1D3A8A)
                                ),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 6.dp)
                            )

                            Spacer(modifier = Modifier.height(12.dp))

                            Box(modifier = Modifier.padding(vertical = 6.dp)) {
                                OutlinedTextField(
                                    value = selectedStatus,
                                    onValueChange = {},
                                    readOnly = true,
                                    label = { Text("학적구분") },
                                    shape = RoundedCornerShape(12.dp),
                                    colors = androidx.compose.material3.TextFieldDefaults.outlinedTextFieldColors(
                                        unfocusedBorderColor = Color(0xFFE0E0E0),
                                        focusedBorderColor = Color(0xFF1D3A8A)
                                    ),
                                    modifier = Modifier.fillMaxWidth(),
                                    trailingIcon = {
                                        IconButton(onClick = { statusExpanded = true }) {
                                            Icon(Icons.Default.ArrowDropDown, contentDescription = "DropDown")
                                        }
                                    }
                                )
                                DropdownMenu(
                                    expanded = statusExpanded,
                                    onDismissRequest = { statusExpanded = false }
                                ) {
                                    listOf("재학", "휴학").forEach {
                                        DropdownMenuItem(
                                            text = { Text(it, color = Color.Black) }, // 텍스트도 검은색
                                            onClick = {
                                                selectedStatus = it
                                                statusExpanded = false
                                            },
                                            modifier = Modifier.background(Color.White) // ✅ 흰색 배경
                                        )
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(12.dp))

                            Box(modifier = Modifier.padding(vertical = 6.dp)) {
                                OutlinedTextField(
                                    value = selectedYear,
                                    onValueChange = {},
                                    readOnly = true,
                                    label = { Text("학년") },
                                    shape = RoundedCornerShape(12.dp),
                                    colors = androidx.compose.material3.TextFieldDefaults.outlinedTextFieldColors(
                                        unfocusedBorderColor = Color(0xFFE0E0E0),
                                        focusedBorderColor = Color(0xFF1D3A8A)
                                    ),
                                    modifier = Modifier.fillMaxWidth(),
                                    trailingIcon = {
                                        IconButton(onClick = { yearExpanded = true }) {
                                            Icon(Icons.Default.ArrowDropDown, contentDescription = "DropDown")
                                        }
                                    }
                                )
                                DropdownMenu(
                                    expanded = yearExpanded,
                                    onDismissRequest = { yearExpanded = false }
                                ) {
                                    listOf("1", "2", "3", "4").forEach {
                                        DropdownMenuItem(
                                            text = { Text(it, color = Color.Black) },
                                            onClick = {
                                                selectedYear = it
                                                yearExpanded = false
                                            },
                                            modifier = Modifier.background(Color.White) // ✅ 흰색 배경
                                        )
                                    }
                                }
                            }
                        }
                    }
                    ,
                    confirmButton = {
                        TextButton(onClick = {
                            showFilter = false
                            // apply filtering logic here
                        }) {
                            Text("적용", color = Color(0xFF1D3A8A))
                        }
                    },
                    dismissButton = {
                        TextButton(onClick = { showFilter = false }) {
                            Text("취소")
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun ScholarshipCard(scholarship: Scholarship) {

    val context = LocalContext.current

    val statusColor = when (scholarship.status) {
        "모집중" -> Color(0xFFD0F5D8)
        "모집전" -> Color(0xFFFFF2CC)
        "모집완료" -> Color(0xFFE0E0E0)
        else -> Color.LightGray
    }

    Card(
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .border(1.dp, Color(0xFFE0E0E0), RoundedCornerShape(12.dp))
            .clickable {
                val intent = Intent(Intent.ACTION_VIEW).apply {
                    data = android.net.Uri.parse(scholarship.link)
                }
                context.startActivity(intent)
            },
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = scholarship.name,
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp,
                    color = Color(0xFF1D3A8A),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f)
                )
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(statusColor)
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(scholarship.status, fontSize = 12.sp, color = Color.Black)
                }
            }
            Spacer(modifier = Modifier.height(6.dp)) // 기존보다 조금 더 큰 여백
            Text(
                "마감일: ${scholarship.deadline}",
                color = Color.Gray,
                fontSize = 13.sp
            )
            Spacer(modifier = Modifier.height(4.dp))

        }
    }
}

@Preview
@Composable
fun PreviewHomeScreen() {
    HomeScreen()
}