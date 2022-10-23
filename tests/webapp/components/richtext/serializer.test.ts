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

  it("Rebuild html title and paragraph", () => {
    const model: any = [
      {
        type: "h1",
        children: [
          {
            text: "Title",
          },
        ],
      },
      {
        type: "paragraph",
        children: [
          {
            text: "My lazy dog",
          },
        ],
      },
      {
        type: "h2",
        children: [
          {
            text: "Subtitle",
          },
        ],
      },
      {
        type: "paragraph",
        children: [
          {
            text: "ha ha!",
          },
        ],
      },
    ];
    const html = toHtml(model);
    expect(html).eql(
      "<h1>Title</h1><p>My lazy dog</p><h2>Subtitle</h2><p>ha ha!</p>"
    );
  });
});
