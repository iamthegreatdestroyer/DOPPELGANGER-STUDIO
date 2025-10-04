// DOPPELGANGER STUDIO - MongoDB Initialization Script
// Schema definitions for document-based data

// Switch to doppelganger database
db = db.getSiblingDB("doppelganger");

// =======================
// COLLECTIONS
// =======================

// Research data (scraped from Wikipedia, TMDB, etc.)
db.createCollection("research_data", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["show_id", "source", "data", "scraped_at"],
      properties: {
        show_id: {
          bsonType: "string",
          description: "Reference to PostgreSQL show ID",
        },
        source: {
          bsonType: "string",
          enum: ["wikipedia", "tmdb", "imdb", "tvdb"],
          description: "Source of research data",
        },
        data: {
          bsonType: "object",
          description: "Scraped data (flexible schema)",
        },
        scraped_at: {
          bsonType: "date",
          description: "When data was scraped",
        },
      },
    },
  },
});

// AI analysis results
db.createCollection("ai_analysis", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["entity_id", "entity_type", "analysis_type", "results"],
      properties: {
        entity_id: {
          bsonType: "string",
          description: "ID of analyzed entity",
        },
        entity_type: {
          bsonType: "string",
          enum: ["show", "character", "episode", "script"],
          description: "Type of entity",
        },
        analysis_type: {
          bsonType: "string",
          enum: [
            "personality_traits",
            "humor_patterns",
            "narrative_structure",
            "relationship_dynamics",
            "visual_style",
            "dialogue_patterns",
          ],
          description: "Type of analysis performed",
        },
        results: {
          bsonType: "object",
          description: "Analysis results",
        },
        confidence_score: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 1.0,
        },
        model_used: {
          bsonType: "string",
          description: "AI model used for analysis",
        },
        created_at: {
          bsonType: "date",
        },
      },
    },
  },
});

// Asset embeddings (CLIP, etc.)
db.createCollection("asset_embeddings", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["asset_id", "embedding_type", "embedding_vector"],
      properties: {
        asset_id: {
          bsonType: "string",
          description: "Reference to asset ID",
        },
        embedding_type: {
          bsonType: "string",
          enum: ["clip_visual", "clip_text", "audio_mfcc", "audio_mel"],
          description: "Type of embedding",
        },
        embedding_vector: {
          bsonType: "array",
          items: {
            bsonType: "double",
          },
          description: "Embedding vector",
        },
        model_version: {
          bsonType: "string",
        },
        created_at: {
          bsonType: "date",
        },
      },
    },
  },
});

// Transformation rules and patterns
db.createCollection("transformation_patterns", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["pattern_type", "source_context", "target_context", "rules"],
      properties: {
        pattern_type: {
          bsonType: "string",
          enum: [
            "character_name",
            "character_form",
            "setting_adaptation",
            "dialogue_style",
            "humor_translation",
          ],
        },
        source_context: {
          bsonType: "object",
          description: "Original context details",
        },
        target_context: {
          bsonType: "object",
          description: "Target context details",
        },
        rules: {
          bsonType: "array",
          items: {
            bsonType: "object",
          },
          description: "Transformation rules",
        },
        success_rate: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 1.0,
        },
        usage_count: {
          bsonType: "int",
          minimum: 0,
        },
        created_at: {
          bsonType: "date",
        },
        updated_at: {
          bsonType: "date",
        },
      },
    },
  },
});

// Performance metrics
db.createCollection("performance_metrics", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["metric_type", "timestamp", "value"],
      properties: {
        metric_type: {
          bsonType: "string",
          enum: [
            "scraping_duration",
            "generation_duration",
            "rendering_duration",
            "api_latency",
            "cache_hit_rate",
            "quality_score",
          ],
        },
        entity_id: {
          bsonType: "string",
          description: "Related entity if applicable",
        },
        timestamp: {
          bsonType: "date",
        },
        value: {
          bsonType: "double",
        },
        metadata: {
          bsonType: "object",
        },
      },
    },
  },
});

// Cache for AI responses
db.createCollection("ai_cache", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["cache_key", "response", "created_at", "expires_at"],
      properties: {
        cache_key: {
          bsonType: "string",
          description: "Hash of prompt + model",
        },
        model: {
          bsonType: "string",
        },
        prompt: {
          bsonType: "string",
        },
        response: {
          description: "Cached response (any type)",
        },
        hit_count: {
          bsonType: "int",
          minimum: 0,
        },
        created_at: {
          bsonType: "date",
        },
        expires_at: {
          bsonType: "date",
        },
      },
    },
  },
});

// =======================
// INDEXES
// =======================

// Research data indexes
db.research_data.createIndex({ show_id: 1, source: 1 });
db.research_data.createIndex({ scraped_at: -1 });

// AI analysis indexes
db.ai_analysis.createIndex({ entity_id: 1, analysis_type: 1 });
db.ai_analysis.createIndex({ created_at: -1 });
db.ai_analysis.createIndex({ confidence_score: -1 });

// Asset embeddings indexes
db.asset_embeddings.createIndex({ asset_id: 1, embedding_type: 1 });

// Transformation patterns indexes
db.transformation_patterns.createIndex({ pattern_type: 1 });
db.transformation_patterns.createIndex({ success_rate: -1 });
db.transformation_patterns.createIndex({ usage_count: -1 });

// Performance metrics indexes
db.performance_metrics.createIndex({ metric_type: 1, timestamp: -1 });
db.performance_metrics.createIndex({ timestamp: -1 });

// AI cache indexes
db.ai_cache.createIndex({ cache_key: 1 }, { unique: true });
db.ai_cache.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });
db.ai_cache.createIndex({ hit_count: -1 });

// =======================
// SAMPLE DATA
// =======================

// Insert sample research data
db.research_data.insertOne({
  show_id: "00000000-0000-0000-0000-000000000000",
  source: "wikipedia",
  data: {
    title: "Test Show",
    description: "Sample show for testing",
    episodes: 100,
    years: "1950-1960",
  },
  scraped_at: new Date(),
});

// Insert sample transformation pattern
db.transformation_patterns.insertOne({
  pattern_type: "character_name",
  source_context: {
    setting: "modern",
    culture: "american",
  },
  target_context: {
    setting: "space",
    culture: "futuristic",
  },
  rules: [
    {
      pattern: "ends_with_y",
      transformation: "replace_with_a",
      examples: ["Lucy -> Luna", "Betty -> Beta"],
    },
  ],
  success_rate: 0.85,
  usage_count: 0,
  created_at: new Date(),
  updated_at: new Date(),
});

print("MongoDB initialization complete!");
print("Collections created:", db.getCollectionNames());
