# Makefile to create results folder in the current directory

# Variables
DIR_NAME = data
RESULTS_DIR = processed          
TARGET_DIR = .

# Default target
all: create_directories

# Target to create the directories
create_directories:
	mkdir -p $(TARGET_DIR)/$(DIR_NAME)/$(RESULTS_DIR)

# Clean target to remove the created directories
clean:
	rm -rf $(TARGET_DIR)/$(DIR_NAME)

.PHONY: all create_directories clean
