import { expect } from "chai";

import { toHtml } from "../../../../src/webapp/ui/components/richtext/serializer";
import { SlateModel } from "../../../../src/webapp/ui/components/richtext/types";

describe("Convert Html to slate model", () => {
  it("Rebuild html paragraph extract the text", () => {
    const model: SlateModel = [
      {
        children: [
          {
            text: "My lazy dog",
          },
        ],
        type: "paragraph",
      },
    ];
    const html = toHtml(model);
    expect(html).eql("<p>My lazy dog</p>");
  });

  it("Rebuild html paragraph extract the bold text", () => {
    const model: any = [
      {
        children: [
          {
            text: "My ",
          },
          {
            text: "lazy",
            bold: true,
          },
          {
            text: " dog",
          },
        ],
        type: "paragraph",
      },
    ];
    const html = toHtml(model);
    expect(html).eql("<p>My <strong>lazy</strong> dog</p>");
  });

});
