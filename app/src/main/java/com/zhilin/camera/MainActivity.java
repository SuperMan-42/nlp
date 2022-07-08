package com.zhilin.camera;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends AppCompatActivity {

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    findViewById(R.id.bt_click).setOnClickListener(view -> {
      if (!Python.isStarted()) {
        Python.start(new AndroidPlatform(this));
      }
      Python py = Python.getInstance();
      py.getModule("textSimilarityDeploy/performanceTest").callAttr("test");
    });
  }
}