package com.example.upstair_dev.home

import android.content.Intent
import androidx.compose.ui.platform.LocalContext
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
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
                        BadgedBox(badge = { Badge { Text("3") } }) {
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
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .padding(horizontal = 16.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(Color(0xFFF2F4F7))
                    .padding(12.dp)
                    .fillMaxWidth()
            ) {
                Image(
                    painter = painterResource(id = R.drawable.robot),
                    contentDescription = "Chatbot",
                    modifier = Modifier.size(40.dp) // 원하는 사이즈 지정
                )
                Spacer(modifier = Modifier.width(8.dp))
                androidx.compose.material3.TextField(
                    value = searchText,
                    onValueChange = { searchText = it },
                    placeholder = { Text("장학금을 검색해보세요...") },
                    colors = androidx.compose.material3.TextFieldDefaults.colors(
                        unfocusedContainerColor = Color.Transparent,
                        focusedContainerColor = Color.Transparent
                    ),
                    modifier = Modifier
                        .weight(1f)
                        .padding(end = 8.dp)
                )
                Icon(Icons.Default.Search, contentDescription = "Search", tint = Color(0xFF1D3A8A))
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
                Text("추천 장학금", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                IconButton(onClick = { showFilter = true }) {
                    Icon(
                        painter = painterResource(id = R.drawable.filter),
                        contentDescription = "Filter"
                    )
                }
            }

            // 장학금 리스트
            LazyColumn(contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)) {
                items(sampleScholarships) { scholarship ->
                    ScholarshipCard(scholarship)
                }
            }

            if (showFilter) {
                AlertDialog(
                    onDismissRequest = { showFilter = false },
                    title = { Text("필터 설정", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = Color(0xFF1D3A8A)) },
                    text = {
                        var grade by remember { mutableStateOf("") }
                        var statusExpanded by remember { mutableStateOf(false) }
                        var yearExpanded by remember { mutableStateOf(false) }
                        var selectedStatus by remember { mutableStateOf("재학생") }
                        var selectedYear by remember { mutableStateOf("1학년") }

                        Column {
                            OutlinedTextField(
                                value = grade,
                                onValueChange = { grade = it },
                                label = { Text("학점 (최대 4.5)") },
                                placeholder = { Text("예: 3.5") },
                                modifier = Modifier.fillMaxWidth()
                            )

                            Spacer(modifier = Modifier.height(8.dp))

                            Box {
                                OutlinedTextField(
                                    value = selectedStatus,
                                    onValueChange = {},
                                    readOnly = true,
                                    label = { Text("학적구분") },
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
                                    listOf("재학생", "휴학생", "졸업생").forEach {
                                        DropdownMenuItem(text = { Text(it) }, onClick = {
                                            selectedStatus = it
                                            statusExpanded = false
                                        })
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(8.dp))

                            Box {
                                OutlinedTextField(
                                    value = selectedYear,
                                    onValueChange = {},
                                    readOnly = true,
                                    label = { Text("학년") },
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
                                    listOf("1학년", "2학년", "3학년", "4학년").forEach {
                                        DropdownMenuItem(text = { Text(it) }, onClick = {
                                            selectedYear = it
                                            yearExpanded = false
                                        })
                                    }
                                }
                            }
                        }
                    },
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

data class Scholarship(val name: String, val deadline: String, val status: String)

val sampleScholarships = listOf(
    Scholarship("국가우수장학금", "2024-03-15", "모집중"),
    Scholarship("성적우수장학금", "2024-04-01", "모집전"),
    Scholarship("저소득층지원장학금", "2024-03-20", "모집중"),
    Scholarship("지역인재장학금", "2024-02-28", "모집완료"),
    Scholarship("창업지원장학금", "2024-03-25", "모집중")
)

@Composable
fun ScholarshipCard(scholarship: Scholarship) {
    val statusColor = when (scholarship.status) {
        "모집중" -> Color(0xFFD0F5D8)
        "모집전" -> Color(0xFFFFF2CC)
        else -> Color(0xFFE0E0E0)
    }

    Card(
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .border(1.dp, Color(0xFFE0E0E0), RoundedCornerShape(12.dp)),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(scholarship.name, fontWeight = FontWeight.Bold)
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(statusColor)
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(scholarship.status, fontSize = 12.sp, color = Color.Black)
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text("마감일: ${scholarship.deadline}", color = Color.Gray, fontSize = 13.sp)
            Spacer(modifier = Modifier.height(8.dp))

        }
    }
}

@Preview
@Composable
fun PreviewHomeScreen() {
    HomeScreen()
}