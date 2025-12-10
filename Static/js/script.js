$(document).ready(function() {
    let jsonData = [];

    $("#uploadFile").change(function(event) {
        let formData = new FormData();
        formData.append("file", event.target.files[0]);

        $.ajax({
            url: "/upload",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                jsonData = response.layers;
                renderTable();
            }
        });
    });

    function renderTable() {
        let tableBody = $("#jsonTableBody");
        tableBody.html("");
        jsonData.forEach((layer, index) => {
            let row = `<tr>
                <td>${layer.name}</td>
                <td><input type="number" value="${layer.x}" class="form-control" data-index="${index}" data-key="x"></td>
                <td><input type="number" value="${layer.y}" class="form-control" data-index="${index}" data-key="y"></td>
                <td><input type="number" value="${layer.width}" class="form-control" data-index="${index}" data-key="width"></td>
                <td><input type="number" value="${layer.height}" class="form-control" data-index="${index}" data-key="height"></td>
                <td><input type="text" value="${layer.font}" class="form-control" data-index="${index}" data-key="font"></td>
                <td><input type="text" value="${layer.justification}" class="form-control" data-index="${index}" data-key="justification"></td>
                <td><input type="color" value="${layer.color}" class="form-control" data-index="${index}" data-key="color"></td>
                <td><input type="text" value="${layer.text}" class="form-control" data-index="${index}" data-key="text"></td>
            </tr>`;
            tableBody.append(row);
        });
    }

    $("#saveJson").click(function() {
        $.post("/save_json", JSON.stringify({ name: "edited_json", layers: jsonData }), function(response) {
            alert(response.message);
        }, "json");
    });

    $(document).on("input", ".form-control", function() {
        let index = $(this).data("index");
        let key = $(this).data("key");
        jsonData[index][key] = $(this).val();
    });
});
