#pragma once

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <stdint.h>

int status = WL_IDLE_STATUS;

typedef struct {
  long file_num;
  int16_t response_code;
} FileNumResponse;

int reconnect(const char* ssid, const char* password) {
  return WiFi.begin(ssid, password);
}

void wifi_scan(){
  int n = WiFi.scanNetworks(); // Scan for networks
  Serial.println("Scan done");
  if (n == 0) {
    Serial.println("No networks found");
  } else {
    Serial.print(n);
    Serial.println(" networks found");
    for (int i = 0; i < n; ++i) {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i)); // SSID
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i)); // Signal strength
    }
  }
}

void writeWavHeader(uint8_t* header, uint32_t dataSize, uint32_t sampleRate) {
  uint32_t fileSize = dataSize + 36;        // Total file size - 8
  uint16_t bitsPerSample = 24;
  uint16_t numChannels = 1;
  uint32_t byteRate = sampleRate * numChannels * (bitsPerSample / 8);
  uint16_t blockAlign = numChannels * (bitsPerSample / 8);
  
  // RIFF header (12 bytes)
  header[0]  = 'R'; header[1]  = 'I'; header[2]  = 'F'; header[3]  = 'F';
  header[4]  = (fileSize & 0xff);       header[5]  = ((fileSize >>  8) & 0xff);
  header[6]  = ((fileSize >> 16) & 0xff); header[7]  = ((fileSize >> 24) & 0xff);
  header[8]  = 'W'; header[9]  = 'A'; header[10] = 'V'; header[11] = 'E';
  
  // fmt chunk (24 bytes)
  header[12] = 'f'; header[13] = 'm'; header[14] = 't'; header[15] = ' ';
  header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0;
  header[20] = 1;  header[21] = 0;                    // PCM format
  header[22] = numChannels; header[23] = 0;
  header[24] = (sampleRate & 0xff);       header[25] = ((sampleRate >>  8) & 0xff);
  header[26] = ((sampleRate >> 16) & 0xff); header[27] = ((sampleRate >> 24) & 0xff);
  header[28] = (byteRate & 0xff);         header[29] = ((byteRate >>  8) & 0xff);
  header[30] = ((byteRate >> 16) & 0xff); header[31] = ((byteRate >> 24) & 0xff);
  header[32] = blockAlign; header[33] = 0;
  header[34] = bitsPerSample; header[35] = 0;
  
  // Data chunk header (8 bytes)
  header[36] = 'd'; header[37] = 'a'; header[38] = 't'; header[39] = 'a';
  header[40] = (dataSize & 0xff);       header[41] = ((dataSize >>  8) & 0xff);
  header[42] = ((dataSize >> 16) & 0xff); header[43] = ((dataSize >> 24) & 0xff);
}

int upload_audio(HTTPClient& database, WiFiClientSecure& secure_client, const String& path, uint8_t* buffer, size_t size, const String access_key){
  uint8_t header[44];
  writeWavHeader(header, size, 16000);
  database.begin(secure_client, path);
  database.addHeader("Content-Type", "audio/wav");
  database.addHeader("X-API-Key", access_key);
  uint8_t* fullfile = (uint8_t*)malloc(44+size);
  memcpy(fullfile, header, 44);
  memcpy(fullfile+44, buffer, size);
  int code = database.PUT(fullfile, size+44);
  String response = database.getString();
  // Serial.printf("HTTP %d, %s\n", code, response.c_str());
  free(fullfile);
  database.end();
  return code;
}

FileNumResponse get_filenum(HTTPClient &server, WiFiClientSecure& secure_client, const String& path, const String access_key) {
  server.begin(secure_client, path);
  server.addHeader("X-API-Key", access_key);
  int16_t code = server.GET();
  String payload = server.getString();
  FileNumResponse response = {payload.toInt(), code};
  return response;
}