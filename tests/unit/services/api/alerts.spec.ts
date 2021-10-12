/**
 * @jest-environment node
 */

import alert from "../../../../services/api/alerts";

describe("/alert API calls", () => {
  it("will raise an error when getAll is called (not a valid or implemented endpoint)", async () => {
    await expect(alert.getAll()).rejects.toEqual(new Error("Not implemented."));
  });
});
