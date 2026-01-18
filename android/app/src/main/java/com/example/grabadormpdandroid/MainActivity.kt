package com.example.grabadormpdandroid

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.io.*
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    private lateinit var etUrl: EditText
    private lateinit var etNombre: EditText
    private lateinit var etKid: EditText
    private lateinit var etKey: EditText
    private lateinit var etPath: EditText
    private lateinit var btnStart: Button
    private lateinit var btnStop: Button
    private lateinit var btnSavePreset: Button
    private lateinit var spinnerPresets: Spinner
    private lateinit var btnLoadPreset: Button
    private lateinit var btnDeletePreset: Button
    private lateinit var tvConsole: TextView

    private var process: Process? = null
    private val executor = Executors.newSingleThreadExecutor()
    private val handler = Handler(Looper.getMainLooper())
    private val presets = mutableListOf<String>()
    private lateinit var adapter: ArrayAdapter<String>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        etNombre = findViewById(R.id.etNombre)
        etKid = findViewById(R.id.etKid)
        etKey = findViewById(R.id.etKey)
        etPath = findViewById(R.id.etPath)
        btnStart = findViewById(R.id.btnStart)
        btnStop = findViewById(R.id.btnStop)
        btnSavePreset = findViewById(R.id.btnSavePreset)
        spinnerPresets = findViewById(R.id.spinnerPresets)
        btnLoadPreset = findViewById(R.id.btnLoadPreset)
        btnDeletePreset = findViewById(R.id.btnDeletePreset)
        tvConsole = findViewById(R.id.tvConsole)

        adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, presets)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        spinnerPresets.adapter = adapter

        loadPresets()

        btnStart.setOnClickListener { startRecording() }
        btnStop.setOnClickListener { stopRecording() }
        btnSavePreset.setOnClickListener { savePreset() }
        btnLoadPreset.setOnClickListener { loadSelectedPreset() }
        btnDeletePreset.setOnClickListener { deleteSelectedPreset() }

        // Extraer binario
        extractBinary()
    }

    private fun extractBinary() {
        try {
            val assetManager = assets
            val input = assetManager.open("N_m3u8DL-RE")
            val outFile = File(filesDir, "N_m3u8DL-RE")
            input.copyTo(outFile.outputStream())
            outFile.setExecutable(true)
        } catch (e: Exception) {
            tvConsole.append("Error extrayendo binario: ${e.message}\n")
        }
    }

    private fun startRecording() {
        val url = etUrl.text.toString()
        if (url.isEmpty()) {
            Toast.makeText(this, "Falta la URL", Toast.LENGTH_SHORT).show()
            return
        }

        val timestamp = System.currentTimeMillis().toString()
        val name = "Grabacion_$timestamp"
        val path = etPath.text.toString().ifEmpty { getExternalFilesDir(null)?.absolutePath ?: "/sdcard" }

        val command = mutableListOf("${filesDir}/N_m3u8DL-RE", url, "--save-name", name, "--save-dir", path, "--auto-select", "--live-pipe-mux")
        if (etKid.text.isNotEmpty() && etKey.text.isNotEmpty()) {
            command.add("--key")
            command.add("${etKid.text}:${etKey.text}")
        }

        btnStart.isEnabled = false
        btnStop.isEnabled = true
        tvConsole.append("Iniciando grabación: $name\n")

        executor.execute {
            try {
                val pb = ProcessBuilder(command).redirectErrorStream(true)
                process = pb.start()
                val reader = BufferedReader(InputStreamReader(process!!.inputStream))
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    handler.post { tvConsole.append("$line\n") }
                }
                process?.waitFor()
                handler.post { onProcessEnd() }
            } catch (e: Exception) {
                handler.post { tvConsole.append("Error: ${e.message}\n") }
            }
        }
    }

    private fun stopRecording() {
        process?.destroy()
        process = null
        tvConsole.append("Grabación parada.\n")
        btnStart.isEnabled = true
        btnStop.isEnabled = false
    }

    private fun onProcessEnd() {
        process = null
        btnStart.isEnabled = true
        btnStop.isEnabled = false
        tvConsole.append("--- GRABACIÓN FINALIZADA ---\n")
    }

    private fun savePreset() {
        val nombre = etNombre.text.toString()
        if (nombre.isEmpty()) {
            Toast.makeText(this, "Ingresa un nombre", Toast.LENGTH_SHORT).show()
            return
        }
        val prefs = getSharedPreferences("presets", MODE_PRIVATE)
        val editor = prefs.edit()
        val preset = JSONObject().apply {
            put("url", etUrl.text.toString())
            put("kid", etKid.text.toString())
            put("key", etKey.text.toString())
            put("path", etPath.text.toString())
        }
        editor.putString(nombre, preset.toString())
        editor.apply()
        loadPresets()
        Toast.makeText(this, "Preset guardado", Toast.LENGTH_SHORT).show()
    }

    private fun loadPresets() {
        val prefs = getSharedPreferences("presets", MODE_PRIVATE)
        presets.clear()
        presets.addAll(prefs.all.keys)
        adapter.notifyDataSetChanged()
    }

    private fun loadSelectedPreset() {
        val nombre = spinnerPresets.selectedItem?.toString() ?: return
        val prefs = getSharedPreferences("presets", MODE_PRIVATE)
        val presetStr = prefs.getString(nombre, "") ?: return
        val preset = JSONObject(presetStr)
        etUrl.setText(preset.optString("url"))
        etNombre.setText(nombre)
        etKid.setText(preset.optString("kid"))
        etKey.setText(preset.optString("key"))
        etPath.setText(preset.optString("path"))
    }

    private fun deleteSelectedPreset() {
        val nombre = spinnerPresets.selectedItem?.toString() ?: return
        val prefs = getSharedPreferences("presets", MODE_PRIVATE)
        val editor = prefs.edit()
        editor.remove(nombre)
        editor.apply()
        loadPresets()
        Toast.makeText(this, "Preset eliminado", Toast.LENGTH_SHORT).show()
    }
}