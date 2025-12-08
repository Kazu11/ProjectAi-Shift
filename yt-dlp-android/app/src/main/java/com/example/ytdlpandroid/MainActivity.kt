package com.example.ytdlpandroid

import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {

    private lateinit var etUrl: EditText
    private lateinit var btnDownload: Button
    private lateinit var tvStatus: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        btnDownload = findViewById(R.id.btnDownload)
        tvStatus = findViewById(R.id.tvStatus)

        // Start Python
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }

        btnDownload.setOnClickListener {
            startDownload()
        }
    }

    private fun startDownload() {
        val url = etUrl.text.toString().trim()
        if (url.isEmpty()) {
            tvStatus.text = "Status: Please enter a URL."
            return
        }

        tvStatus.text = "Status: Starting download..."

        // Run network and file operations in a background thread
        CoroutineScope(Dispatchers.IO).launch {
            // Get the app-specific Downloads directory on external storage.
            // This is compatible with Scoped Storage and doesn't require special permissions.
            val downloadsDirFile = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)

            if (downloadsDirFile == null) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Status: External storage is not available."
                }
                return@launch
            }
            val downloadsDir = downloadsDirFile.absolutePath

            val py = Python.getInstance()
            val downloaderModule = py.getModule("downloader")

            val result = try {
                downloaderModule.callAttr("download_video", url, downloadsDir).toString()
            } catch (e: Exception) {
                // To get a more detailed error from Python
                val pythonError = e.message
                "Error: $pythonError"
            }

            // Update UI on the main thread
            withContext(Dispatchers.Main) {
                tvStatus.text = "Status: $result"
            }
        }
    }
}
