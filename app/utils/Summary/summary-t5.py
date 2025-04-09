import unittest
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from pathlib import Path

class TestBartSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_name = "mrm8488/t5-base-finetuned-summarize-news"  # Updated model name
        cls.model_path = Path("../../models/summary")  # Relative path to save the model

        # Ensure the directory exists
        cls.model_path.mkdir(parents=True, exist_ok=True)

        print(f"Model path: {cls.model_path}")  # Print the model path for verification
        print(f"Model path (absolute): {cls.model_path.resolve()}")  # Print absolute path for verification

        try:
            # Load tokenizer and model directly into the specified path
            cls.tokenizer = AutoTokenizer.from_pretrained(
                cls.model_name,
                cache_dir=str(cls.model_path)  # Specify cache directory
            )
            cls.model = AutoModelForSeq2SeqLM.from_pretrained(
                cls.model_name,
                cache_dir=str(cls.model_path)  # Specify cache directory
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model or tokenizer: {e}")

        # Check if the model files exist in the specified directory
        if not any(cls.model_path.iterdir()):
            raise FileNotFoundError(f"Model files not found in {cls.model_path}. Ensure the model is downloaded correctly.")

        if torch.cuda.is_available():
            cls.model.cuda()
            cls.device = "cuda"
        else:
            cls.device = "cpu"

    def test_summary(self):
        text = """NASA has officially announced that Artemis II, the second mission in the Artemis program and the first to carry astronauts around the Moon since the Apollo era, is scheduled for launch in September 2025. The mission will mark the first time humans have traveled to the vicinity of the Moon since Apollo 17 in 1972.

The Artemis II crew, which includes three NASA astronauts and one Canadian Space Agency astronaut, will orbit the Moon without landing. Their primary goal is to test NASA’s new deep space transportation systems, including the Space Launch System (SLS) rocket and the Orion spacecraft, in preparation for a future lunar landing with Artemis III.

During the 10-day mission, astronauts will perform rigorous tests on Orion’s life support, navigation, and communication systems. This mission will also serve as a critical milestone for validating the spacecraft’s performance in the deep-space environment before committing to a surface landing.

NASA Administrator Bill Nelson said in a press briefing, “With Artemis II, we are stepping into a new era of space exploration. Our astronauts will travel farther than any humans have ever been from Earth, paving the way for long-term lunar presence and eventually Mars.”

If Artemis II is successful, Artemis III could launch as early as 2026 and would include the first woman and first person of color to walk on the Moon, using SpaceX’s Starship as the lunar lander.

The Artemis program is part of NASA’s broader effort to establish a sustainable human presence on the Moon and to use it as a stepping stone for future crewed missions to Mars in the 2030s."""
        formatted_text = "vietnews: " + text + " </s>"

        encoding = self.tokenizer(formatted_text, return_tensors="pt")
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=400,
            min_length=100,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True
        )

        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        print("Generated Summary:", summary)

if __name__ == "__main__":
    unittest.main()
