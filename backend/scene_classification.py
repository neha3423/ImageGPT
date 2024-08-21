import torch
from skimage import io

class ResNetAID:
    def __init__(self, device=None):
        print("Initializing SceneClassification")
        from torchvision import models
        self.model = models.resnet34(pretrained=False, num_classes=30)
        self.device = device
        trained = torch.load(r'./checkpoints/Resnet34_best.pth', map_location=torch.device('cpu'))

        self.model.load_state_dict(trained)
        self.model = self.model.to(device)
        self.model.eval()
        self.mean, self.std = torch.tensor([123.675, 116.28, 103.53]).reshape((1, 3, 1, 1)), torch.tensor(
            [58.395, 57.12, 57.375]).reshape((1, 3, 1, 1))
        self.all_dict = {'Bridge': 0, 'Medium Residential': 1, 'Park': 2, 'Stadium': 3, 'Church': 4,
                         'Dense Residential': 5, 'Farmland': 6,
                         'River': 7, 'School': 8, 'Sparse Residential': 9, 'Viaduct': 10, 'Beach': 11, 'Forest': 12,
                         'Baseball Field': 13, 'Desert': 14, 'BareLand': 15,
                         'Railway Station': 16, 'Center': 17, 'Industrial': 18, 'Meadow': 19, 'Airport': 20,
                         'Storage Tanks': 21, 'Pond': 22, 'Commercial': 23, 'Resort': 24,
                         'Parking': 25, 'Port': 26, 'Square': 27, 'Mountain': 28, 'Playground': 29}


    def predict(self, inputs):
        image_path = inputs
        image = torch.from_numpy(io.imread(image_path))
        image = (image.permute(2, 0, 1).unsqueeze(0) - self.mean) / self.std
        with torch.no_grad():
            pred = self.model(image.to(self.device))

        values, indices = torch.softmax(pred, 1).topk(2, dim=1, largest=True, sorted=True)
        output_txt = 'This image' + ' has ' + str(
            torch.round(values[0][0] * 10000).item() / 100) + '% probability being ' + list(self.all_dict.keys())[
                         indices[0][0]] + '.'
        print(f"\nProcessed Scene Classification, Input Image: {inputs}, Output Scene: {output_txt}")
        return output_txt


# import torch
# from skimage import io

# class ResNetAID:
#     def __init__(self, device=None):
#         print("Initializing SceneClassification")
#         from torchvision import models
#         self.model = models.resnet50(pretrained=False, num_classes=30)  # Use ResNet-50 to match the checkpoint
#         self.device = device
        #model_path = r'C:\ImageGPT\Scene Classification\resnet50_checkpoint.pth'  # Replace with your actual model path
#         trained = torch.load(model_path)
#         self.model.load_state_dict(trained)
#         self.model = self.model.to(device)
#         self.model.eval()
#         self.mean, self.std = torch.tensor([123.675, 116.28, 103.53]).reshape((1, 3, 1, 1)), torch.tensor(
#             [58.395, 57.12, 57.375]).reshape((1, 3, 1, 1))
#         self.class_names = {
#             0: 'Airport', 1: 'BareLand', 2: 'Baseball Field', 3: 'Beach', 4: 'Bridge', 
#             5: 'Center', 6: 'Church', 7: 'Commercial', 8: 'Dense Residential', 9: 'Desert', 
#             10: 'Farmland', 11: 'Forest', 12: 'Industrial', 13: 'Meadow', 14: 'Medium Residential', 
#             15: 'Mountain', 16: 'Park', 17: 'Parking', 18: 'Playground', 19: 'Pond', 
#             20: 'Port', 21: 'Railway Station', 22: 'Resort', 23: 'River', 24: 'School', 
#             25: 'Sparse Residential', 26: 'Square', 27: 'Stadium', 28: 'Storage Tanks', 29: 'Viaduct'
#         }
    
#     def predict(self, inputs):
#         image_path = inputs
#         image = torch.from_numpy(io.imread(image_path))
#         image = (image.permute(2, 0, 1).unsqueeze(0) - self.mean) / self.std
#         with torch.no_grad():
#             pred = self.model(image.to(self.device))

#         values, indices = torch.softmax(pred, 1).topk(2, dim=1, largest=True, sorted=True)
#         output_txt = image_path + ' has ' + str(
#             torch.round(values[0][0] * 10000).item() / 100) + '% probability being ' + self.class_names[
#                          indices[0][0].item()] + '.'
#         return output_txt

# Example usage:
if __name__ == "__main__":
    #model_path = r'C:\ImageGPT\Scene Classification\resnet50_checkpoint.pth'  # Replace with your actual model path
    resnet_aid = ResNetAID()
    img_path = r'C:\ImageGPT\scene classification(old)\aid_test\test39.jpg'  # Replace with the path to your dynamic image
    predicted_class = resnet_aid.predict(img_path)
    print(f"Predicted scene class: {predicted_class}")