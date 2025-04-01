import os
import torch
import torchvision.transforms as transforms
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from sklearn.metrics import classification_report
from model import SimpleNN

transform = transforms.Compose([
    transforms.Resize((28, 28)),  
    transforms.ToTensor(),         
    transforms.Normalize((0.5,), (0.5,))  
])

class CustomDataset(Dataset):
    def __init__(self, image_dir, transform=None):
        self.image_dir = image_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        
        for filename in os.listdir(image_dir):
            if filename.endswith('.png'):
                label = int(filename[0])
                self.image_paths.append(os.path.join(image_dir, filename))
                self.labels.append(label)
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        image = Image.open(image_path).convert('L')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

test_dir = './mydigits'
test_dataset = CustomDataset(test_dir, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleNN().to(device)
model.load_state_dict(torch.load('model_1.pth'))
model.eval()

y_true, y_pred = [], []
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images) 
        _, predicted = torch.max(outputs, 1) 
        y_true.extend(labels.cpu().numpy())
        y_pred.extend(predicted.cpu().numpy())

report = classification_report(y_true, y_pred, digits=4)
print(report)