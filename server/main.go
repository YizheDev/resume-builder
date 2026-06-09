package main

import (
	"embed"
	"fmt"
	"io/fs"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

//go:embed static/*
var staticFiles embed.FS

type Resume struct {
	ID        uint      `json:"id" gorm:"primaryKey"`
	Title     string    `json:"title" gorm:"default:'未命名简历'"`
	Template  string    `json:"template" gorm:"default:'classic'"`
	Data      string    `json:"data"` // JSON string
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

var db *gorm.DB

func main() {
	// 数据库连接
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&parseTime=True",
		getEnv("DB_USER", "root"),
		getEnv("DB_PASS", ""),
		getEnv("DB_HOST", "127.0.0.1"),
		getEnv("DB_PORT", "3306"),
		getEnv("DB_NAME", "resume_builder"),
	)

	var err error
	db, err = gorm.Open(mysql.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("数据库连接失败: %v", err)
	}

	db.AutoMigrate(&Resume{})
	log.Println("数据库连接成功")

	// 路由
	r := gin.Default()

	// API 路由
	api := r.Group("/api")
	{
		api.GET("/resumes", listResumes)
		api.POST("/resumes", createResume)
		api.GET("/resumes/:id", getResume)
		api.PUT("/resumes/:id", updateResume)
		api.DELETE("/resumes/:id", deleteResume)
		api.GET("/health", func(c *gin.Context) {
			c.JSON(200, gin.H{"status": "ok"})
		})
	}

	// 静态文件（前端 SPA）
	staticFS, _ := fs.Sub(staticFiles, "static")
	r.NoRoute(gin.WrapH(http.FileServer(http.FS(staticFS))))

	port := getEnv("PORT", "8080")
	log.Printf("Resume Builder 启动于 :%s", port)
	r.Run(":" + port)
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

// --- Handlers ---

func listResumes(c *gin.Context) {
	var resumes []Resume
	db.Order("updated_at desc").Find(&resumes)
	c.JSON(200, gin.H{"code": 0, "data": resumes})
}

func createResume(c *gin.Context) {
	var r Resume
	if err := c.ShouldBindJSON(&r); err != nil {
		c.JSON(400, gin.H{"code": 1, "message": err.Error()})
		return
	}
	db.Create(&r)
	c.JSON(200, gin.H{"code": 0, "data": r})
}

func getResume(c *gin.Context) {
	var r Resume
	if err := db.First(&r, c.Param("id")).Error; err != nil {
		c.JSON(404, gin.H{"code": 1, "message": "未找到"})
		return
	}
	c.JSON(200, gin.H{"code": 0, "data": r})
}

func updateResume(c *gin.Context) {
	var r Resume
	if err := db.First(&r, c.Param("id")).Error; err != nil {
		c.JSON(404, gin.H{"code": 1, "message": "未找到"})
		return
	}
	var input Resume
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(400, gin.H{"code": 1, "message": err.Error()})
		return
	}
	db.Model(&r).Updates(map[string]interface{}{
		"title":    input.Title,
		"template": input.Template,
		"data":     input.Data,
	})
	c.JSON(200, gin.H{"code": 0, "data": r})
}

func deleteResume(c *gin.Context) {
	db.Delete(&Resume{}, c.Param("id"))
	c.JSON(200, gin.H{"code": 0, "message": "已删除"})
}
