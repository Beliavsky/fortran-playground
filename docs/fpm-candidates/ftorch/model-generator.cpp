#include <torch/script.h>
int main() {
    torch::jit::Module model("Tiny");
    model.define(R"JIT(def forward(self, x):
    return x * 2.0 + 1.0
)JIT");
    model.save("tiny.pt");
}
